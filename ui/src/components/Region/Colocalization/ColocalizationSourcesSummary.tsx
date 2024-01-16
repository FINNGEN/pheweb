
import React, { useState, useEffect } from "react";
import { Colocalization } from "../../../common/commonModel";
import './Colocalization.css'

interface Props {
	readonly data: Colocalization[]| undefined
}

const ColocalizationSourcesSummary = ( props: Props) => {

    const [colocalization, setColocalization] = useState<Colocalization[]| undefined>(props.data);
    const arr = colocalization?.map(element => {return element.source2_displayname});
    const sources = arr.filter((item,index) => arr.indexOf(item) === index);

    useEffect(() => {
        setColocalization
    }, [])

    return (
        <div className="colocs-summary" >
            {sources.map((key, i) => 
                <div className="colocs-summary-text" key={key}>{key}: 
                    <span className="colocs-summary-pos"> <b>↑</b>
                        {colocalization?.filter(element => element.beta2 > 0 && element.source2_displayname == key).length}
                    </span>
                    <span className="colocs-summary-neg"> <b>↑</b>
                        {colocalization?.filter(element => element.beta2 <= 0 && element.source2_displayname == key).length}
                    </span>
            </div>)}
        </div> 
    )

};

export default ColocalizationSourcesSummary;

