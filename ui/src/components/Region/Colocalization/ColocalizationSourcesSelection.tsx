import React, { useState, useEffect } from "react";
import './Colocalization.css'

interface Props {
	readonly sources: string[];
}

const ColocalizationSourcesSummary = ( props: Props) => {

    const [sources, setSources] = useState<string[]>(props.sources);

    return (
        <div className="colocs-summary-selector">
            <form id="colocs-selector" className="colocs-summary-selector">
                <label htmlFor="selectedOptions"/>
                    <span className="colocs-summary-item"><b>Select source(s):</b></span>
                    <select size={1} multiple name = "selectedOptions" onChange = {(e) => {
                        const selected = Array.from(e.target.options).filter(opt => opt.selected).map(opt => opt.value)
                        setSources(selected);
                    }}>
                    {sources.map((key, i) => 
                        <option value={key}>{key}</option>
                    )}
                    </select>
                    <input type="submit" value="Submit" onClick = {(e) => console.log(e.target)}/>
            </form>
        </div>
    )

};

export default ColocalizationSourcesSummary;

