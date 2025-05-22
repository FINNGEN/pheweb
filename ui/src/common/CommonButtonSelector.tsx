import React, {ReactElement, useState} from "react";

interface SelectorProps<T> {
    options: T[];
    onSelect: (value: T | null) => void;
    initial?: (options: T[]) => T; // Function to compute initial value
    emptyElement?: ReactElement;
}

const defaultEmptyElement = <p className="text-gray-500">No options available</p>

const CommonButtonSelector = <T extends string | number>({
                                                             options,
                                                             onSelect,
                                                             initial = (opts) => opts[0], // Default: first element
                                                             emptyElement = defaultEmptyElement
                                                         }: SelectorProps<T>) => {
    const computedInitial = options.length > 0 ? initial(options) : null;
    const [selected, setSelected] = useState<T | null>(computedInitial);

    const handleClick = (value: T) => {
        setSelected(value);
        onSelect(value);
    };

    if (options.length === 0) {
        return emptyElement;
    }

    return (
        <div className="flex gap-2">
            {options.map((option) => (
                <button
                    key={option}
                    className={`px-4 py-2 rounded border ${
                        selected === option ? "bg-gray-200" : "bg-blue-500 text-white"
                    }`}
                    onClick={() => handleClick(option)}
                >
                    {option}
                </button>
            ))}
        </div>
    );
};

export default CommonButtonSelector;