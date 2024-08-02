interface EditableCodeBlockProps {
    isEditable: boolean;
    value: string | null;
    onChange?: (value: string | null) => void;
}

export function EditableCodeBlock({ isEditable, value, onChange }: EditableCodeBlockProps) {
    const getFormattedJsonValue = (value: string | null) => {
        if (!value) {
            return null;
        }

        let parsed = null;
        try {
            parsed = JSON.parse(value);
        } catch (e) {
            return typeof value === "object" ? JSON.stringify(value) : value;
        }
        return JSON.stringify(parsed, null, 2);
    };

    return (
        <pre
            className="whitespace-pre-wrap rounded-md bg-muted p-1 p-2 text-xs text-foreground"
            contentEditable={isEditable}
            suppressContentEditableWarning={true}
            onBlur={(e) => (onChange ? onChange(e.currentTarget.textContent) : null)}
        >
            {getFormattedJsonValue(value)}
        </pre>
    );
}
