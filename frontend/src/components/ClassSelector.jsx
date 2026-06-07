import React, { useMemo, useState } from "react";

export default function ClassSelector({
    classes,
    selectedClasses,
    onChange,
    loading
}) {
    const [search, setSearch] = useState("");

    const filteredClasses = useMemo(() => {
        const query = search.trim().toLowerCase();
        if (!query) {
            return classes;
        }

        return classes.filter((className) => className.toLowerCase().includes(query));
    }, [classes, search]);

    const toggleClass = (className) => {
        if (selectedClasses.includes(className)) {
            onChange(selectedClasses.filter((item) => item !== className));
            return;
        }

        onChange([...selectedClasses, className]);
    };

    const selectFiltered = () => {
        const next = Array.from(new Set([...selectedClasses, ...filteredClasses]));
        onChange(next);
    };

    const clearSelected = () => {
        onChange([]);
    };

    return (
        <section className="panel-row class-selector">
            <div className="selector-header">
                <label className="label">Detected Classes</label>
                <span className="selector-count">{selectedClasses.length} selected</span>
            </div>

            <input
                className="input"
                type="text"
                placeholder="Search classes..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                disabled={loading}
            />

            <div className="selector-actions">
                <button type="button" className="button subtle" onClick={selectFiltered} disabled={loading}>
                    Add filtered
                </button>
                <button type="button" className="button ghost" onClick={clearSelected} disabled={loading}>
                    Clear
                </button>
            </div>

            <div className="selected-chips">
                {selectedClasses.length === 0 ? (
                    <span className="chip muted">No classes selected</span>
                ) : (
                    selectedClasses.map((className) => (
                        <button
                            key={className}
                            type="button"
                            className="chip"
                            onClick={() => toggleClass(className)}
                            disabled={loading}
                            title="Remove"
                        >
                            {className} ×
                        </button>
                    ))
                )}
            </div>

            <div className="class-list" role="listbox" aria-multiselectable="true">
                {filteredClasses.map((className) => {
                    const checked = selectedClasses.includes(className);
                    return (
                        <label key={className} className={`class-item ${checked ? "selected" : ""}`}>
                            <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => toggleClass(className)}
                                disabled={loading}
                            />
                            <span>{className}</span>
                        </label>
                    );
                })}
            </div>
        </section>
    );
}
