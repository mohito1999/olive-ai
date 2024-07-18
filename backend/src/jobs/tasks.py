import io

from celery.schedules import crontab
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from playwright.sync_api import sync_playwright

from celeryworker import celery_app
from config import (
    AWS_REGION,
    SCREENSHOT_DIFF_THRESHOLD,
    SCREENSHOTS_S3_BUCKET_ENDPOINT,
    SCREENSHOTS_S3_BUCKET_NAME,
)
from constants import TestFrequency, TestResultStatus, TestRunState, TestState, TestStepType
from log import log
from models import TestTable
from repositories import TestRepository, TestRunRepository, TestStepRepository
from schemas import TestRunDBInput, TestRunResult, TestRunResultStep
from util.id import get_user_test_id, separate_user_test_id
from util.s3 import S3Helper


@celery_app.task(name="run_test")
def run_test(user_test_id: str, run_id: str):
    log.info(f"Running test for user_test_id: {user_test_id}, run_id: {run_id}")
    user_id, test_id = separate_user_test_id(user_test_id)
    test_run = TestRunRepository().get(user_test_id, run_id)
    log.info(f"Test Run: {test_run}")
    test = TestRepository().get(user_id, test_id)
    log.info(f"Test: {test}")
    test_steps = TestStepRepository().list(user_test_id)
    sorted_test_steps = sorted(test_steps, key=lambda x: x.created_at)
    width = test.device.viewport.width
    height = test.device.viewport.height

    s3 = S3Helper(
        endpoint_url=SCREENSHOTS_S3_BUCKET_ENDPOINT,
        region=AWS_REGION,
        bucket_name=SCREENSHOTS_S3_BUCKET_NAME,
    )

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch()
        context = browser.new_context(
            viewport={
                "width": width,
                "height": height,
            }
        )
        page = context.new_page()

        result_steps = []
        run_failed = False
        for step in sorted_test_steps:
            if run_failed:
                log.info(f"Skipping step: {step.type}")
                result_steps.append(
                    TestRunResultStep(
                        test_step_id=step.id,
                        type=step.type,
                        status=TestResultStatus.SKIPPED,
                        artifacts=[],
                    ),
                )
                continue

            log.info(f"Executing step: {step.type}")
            try:
                match step.type:
                    case TestStepType.NAVIGATION:
                        page.goto(step.location.url, wait_until="domcontentloaded")
                    case TestStepType.CLICK:
                        page.mouse.click(step.click_position.x, step.click_position.y)
                    case TestStepType.SCROLL:
                        page.evaluate(
                            f"window.scrollTo({step.scroll_position.x}, {step.scroll_position.y-1})"
                        )
                    case TestStepType.SCREENSHOT:
                        new_screenshot = page.screenshot()
                        existing_screenshot = s3.download_file(
                            file_path=f"{user_id}/{test_id}",
                            file_name=f"{step.id}.png",
                        )
                        if not existing_screenshot:
                            artifact = {
                                "error": f"Existing screenshot for step {step.id} not found"
                            }
                            result_steps.append(
                                TestRunResultStep(
                                    test_step_id=step.id,
                                    type=step.type,
                                    status=TestResultStatus.FAILED,
                                    artifacts=[artifact],
                                ),
                            )
                            run_failed = True
                            continue

                        existing_image = Image.open(io.BytesIO(existing_screenshot))
                        new_image = Image.open(io.BytesIO(new_screenshot))
                        diff = pixelmatch(existing_image, new_image, None)
                        if diff > SCREENSHOT_DIFF_THRESHOLD:
                            log.info(
                                f"Screenshot diff for test {test_id}, run {run_id}, step {step.id}: {diff}"
                            )
                            response = s3.upload_file(
                                file_path=f"{user_id}/{test_id}/{run_id}",
                                file_name=f"{step.id}.png",
                                body=new_screenshot,
                            )
                            log.info(f"Uploaded screenshot to S3: {response}")
                            url = f"{SCREENSHOTS_S3_BUCKET_ENDPOINT}/{SCREENSHOTS_S3_BUCKET_NAME}/{user_id}/{test_id}/{run_id}/{step.id}.png"
                            log.info(f"Screenshot URL: {url}")
                            artifact = {"url": url}
                            result_steps.append(
                                TestRunResultStep(
                                    test_step_id=step.id,
                                    type=step.type,
                                    status=TestResultStatus.FAILED,
                                    artifacts=[artifact],
                                ),
                            )
                            run_failed = True
                            continue

                result_steps.append(
                    TestRunResultStep(
                        test_step_id=step.id,
                        type=step.type,
                        status=TestResultStatus.PASSED,
                        artifacts=[],
                    ),
                )
            except Exception as e:
                log.exception(e)
                artifact = {"error": str(e)}
                result_steps.append(
                    TestRunResultStep(
                        test_step_id=step.id,
                        type=step.type,
                        status=TestResultStatus.FAILED,
                        artifacts=[artifact],
                    ),
                )
                run_failed = True

        test_run.state = TestRunState.COMPLETED
        test_run.result.status = TestResultStatus.FAILED if run_failed else TestResultStatus.PASSED
        test_run.result.steps = result_steps
        TestRunRepository().update(test_run, user_test_id, run_id)


@celery_app.task(name="complete_test_recording")
def complete_test_recording(user_id: str, test_id: str):
    log.info(f"Completing test recording for user_id: {user_id}, test_id: {test_id}")

    test = TestRepository().get(user_id, test_id)
    log.info(f"Test: {test}")
    test_steps = TestStepRepository().list(get_user_test_id(user_id, test_id))
    sorted_test_steps = sorted(test_steps, key=lambda x: x.created_at)

    s3 = S3Helper(
        endpoint_url=SCREENSHOTS_S3_BUCKET_ENDPOINT,
        region=AWS_REGION,
        bucket_name=SCREENSHOTS_S3_BUCKET_NAME,
    )

    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=test.device.ua,
            viewport={
                "width": test.device.viewport.width,
                "height": test.device.viewport.height,
            },
        )
        page = context.new_page()

        for step in sorted_test_steps:
            log.info(f"Executing step: {step.type}")
            if step.type == TestStepType.NAVIGATION:
                page.goto(step.location.url)
            if step.type == TestStepType.CLICK:
                page.mouse.click(step.click_position.x, step.click_position.y)
            if step.type == TestStepType.SCROLL:
                page.evaluate(
                    f"window.scrollTo({step.scroll_position.x}, {step.scroll_position.y})"
                )
            if step.type == TestStepType.SCREENSHOT:
                screenshot_bytes = page.screenshot()
                response = s3.upload_file(
                    file_path=f"{user_id}/{test_id}",
                    file_name=f"{step.id}.png",
                    body=screenshot_bytes,
                )
                log.info(f"Uploaded screenshot to S3: {response}")
                url = f"{SCREENSHOTS_S3_BUCKET_ENDPOINT}/{SCREENSHOTS_S3_BUCKET_NAME}/{user_id}/{test_id}/{step.id}.png"
                log.info(f"Screenshot URL: {url}")

    test.state = TestState.COMPLETED
    TestRepository().update(test, user_id, test_id)


def queue_tests_to_run(tests):
    for test in tests:
        log.info(f"Queuing test run for user_id: {test.user_id}, test_id: {test.id}")
        user_test_id = get_user_test_id(test.user_id, test.id)
        data = TestRunDBInput(
            user_test_id=user_test_id,
            state=TestRunState.QUEUED,
            result=TestRunResult(status=TestResultStatus.PENDING, steps=[]),
        )
        item = TestRunRepository().create(data)
        run_test.apply_async(
            (user_test_id, item.id),
        )


@celery_app.task(name="run_daily_tests")
def run_daily_tests():
    log.info("Running daily tests")
    tests = TestTable.frequency_index.query(TestFrequency.DAILY.value)
    queue_tests_to_run(tests)


@celery_app.task(name="run_weekly_tests")
def run_weekly_tests():
    log.info("Running weekly tests")
    tests = TestTable.frequency_index.query(TestFrequency.WEEKLY.value)
    queue_tests_to_run(tests)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    log.info(f"Registering periodic tasks on {sender}")
    sender.add_periodic_task(crontab(hour=12, minute=0), run_daily_tests)
    sender.add_periodic_task(crontab(hour=12, minute=0, day_of_week=1), run_weekly_tests)
    log.info(f"Registered periodic tasks on {sender}")
