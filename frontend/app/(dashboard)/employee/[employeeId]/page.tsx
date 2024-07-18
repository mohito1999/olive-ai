import BreadCrumb from '@/components/breadcrumb';
import { ProductForm } from '@/components/forms/product-form';
import { ScrollArea } from '@/components/ui/scroll-area';
import React from 'react';

export default function Page() {
    const breadcrumbItems = [
        { title: 'Employee', link: '/employee' },
        { title: 'Create', link: '/employee/create' }
    ];
    return (
        <ScrollArea className="h-full">
            <div className="flex-1 space-y-4 p-8">
                <BreadCrumb items={breadcrumbItems} />
                <ProductForm
                    categories={[
                        { _id: 'shirts', name: 'shirts' },
                        { _id: 'pants', name: 'pants' }
                    ]}
                    initialData={null}
                    key={null}
                />
            </div>
        </ScrollArea>
    );
}
