import React, { useContext, useEffect, useState } from "react";
import { CasualVariant, Colocalization, variantToStr } from "../../../common/commonModel";
import ReactTable, { Cell, Column, Row } from "react-table-v6";
import { ColocalizationContext, ColocalizationState } from "./ColocalizationContext";
import selectTableHOC from "react-table/lib/hoc/selectTable";
import { CSVLink } from "react-csv";
import { refreshLocusZoom } from "./ColocalizationLocusZoom";
import { RegionContext, RegionState } from "../RegionContext";
import ColocalizationSourcesSummary from './ColocalizationSourcesSummary';
import {colocTypesSummaryData as summaryData} from '../../../common/commonModel'

import './Colocalization.css'
import { colocalizationTable, colocalizationSubtable, createTableColumns } from '../../../common/commonTableColumn';
import { ConfigurationWindow } from '../../Configuration/configurationModel';

declare let window: ConfigurationWindow;

const configuration = window?.config?.userInterface?.region?.colocalization;


const SelectTable = selectTableHOC(ReactTable);
SelectTable.prototype.headSelector = () => null;

interface Metadata { accessor: string
                     label: string
                     title: string
                     Cell? : ((arg: Row<Colocalization>) => JSX.Element) |
                             ((arg: Cell<{},string>) => string) |
                             ((arg: Cell<{},number>) => string)
                     width? : number
                     flexBasis? : string }


const listMetadata : Column[] = createTableColumns(configuration?.tableColumns) || colocalizationTable;
const subComponentMetadata : Column[] = createTableColumns(configuration?.subtableColumns) || colocalizationSubtable;

const columns = (metadata : Metadata[]) => metadata.map(c => ({ ...c , Header: () => (<span title={ c.title} style={{textDecoration: 'underline'}}>{ c.label }</span>) }))
const headers = (metadata : Metadata[]) => columns(metadata).map(c => ({ ...c , key: c.accessor }))

const subComponent = (row : Row<Colocalization>) => {
    const colocalization : Colocalization = row.original;
    const causalvariant : CasualVariant[] = colocalization.variants;

    const reactTable =         <ReactTable
        data={ causalvariant }
        columns={ columns(subComponentMetadata) }
        defaultPageSize={5}
        showPagination={true} />
    return (<div style={{ padding: "20px" }}> { reactTable}</div>);
}


interface Props {}
const ColocalizationList = (props : Props) => {
    const { locusZoomData,
            colocalization ,
            selectedColocalization,
            setSelectedColocalization } = useContext<Partial<ColocalizationState>>(ColocalizationContext);
    const { locusZoomContext ,setSelectedPosition } = useContext<Partial<RegionState>>(RegionContext);

    const [selectedRow, setRowSelected]= useState<string | undefined>(undefined);
    
    const [colocFiltBySource, setColocFiltBySource] = useState<Colocalization[]>([]);
    
    const [selectedSources, setSelectedSources] = useState<(string|undefined)[]>([]);
    const [initialSources, setInitialSources] = useState<(string|undefined)[]>([]);
    const [allChecked, setAllChecked] = useState<boolean>(true);    
    const [showDropdown, setShowDropdown] = useState<boolean>(false);
    const [selectorText, setSelectorText] = useState<string>("Select All");
    const [sourceSummaryData, setSourceSummaryData]  = useState<summaryData[] | undefined>([]);

  useEffect(() => {
      colocalization
      && locusZoomData
      && locusZoomContext
      && setSelectedPosition 
      && refreshLocusZoom(setSelectedPosition,selectedColocalization, locusZoomData, locusZoomContext); },
    [ setSelectedPosition , colocalization , locusZoomData , selectedColocalization, locusZoomContext ]);

    const rowid = selectedRow?.split('-')?.at(-1);

    const toggleSelection = (key : string, shift, row : Colocalization) => {
        const clearSelection = selectedRow !== undefined && selectedRow == key;
        setSelectedColocalization && setSelectedColocalization(clearSelection? undefined : row);
        setRowSelected(	clearSelection ? undefined : key);
    }

    const isSelected = (key : string) => rowid == key || false;

    const rowFn = (state : {}, rowInfo : Row<Colocalization>, column : Column<Colocalization>, instance) => {
        return { onClick: (e : Event, handleOriginal : (undefined | (() => void))) => handleOriginal && handleOriginal() ,
                 style: { background: (rowInfo && selectedRow && rowid == rowInfo.original.colocalization_id)? "lightgrey" : undefined		     }
        };
    };

    const flatten = (c : Colocalization) => { return { ...c ,
                                                       locus_id1 : c.locus_id1?variantToStr(c.locus_id1):undefined } };

    useEffect(() => {
        if (colocalization){
            const arr = colocalization?.map(element => {return element.dataset2}); 
            const src = arr?.filter((item,index) => arr.indexOf(item) === index);
            setInitialSources(src);
            setSelectedSources(src);
            setColocFiltBySource;   
            setSourceSummaryData(colocalization?.map(
                element => { return {source: element['dataset2'], beta: element['beta2'], sourceKey:  element['source2'] }}).sort()
            );

        }  
    }, [colocalization]);

    useEffect(() => {
        if (colocalization){
            setColocFiltBySource(colocalization.filter(element => selectedSources.indexOf(element.dataset2) > -1));
            selectedSources.length == initialSources.length ? setAllChecked(true) : setAllChecked(false);
            selectedSources.length == initialSources.length ? setSelectorText("All Selected") : setSelectorText(selectedSources.length + " Selected");
        }  
    }, [selectedSources]);

    const inputCheckboxAllSources = (
        <>
        <input type="checkbox" id='All' name='All' value='All' checked={allChecked} onChange={(e) => {
            setAllChecked(e.target.checked);
            var src = e.target.checked ? [...initialSources] : [];
            setSelectedSources(src);
        }}/>
        <span className="checkbox-label"><label htmlFor='All'>All</label></span>
        </>
    );

    if(colocalization && locusZoomData && colocFiltBySource){
        return (<div>
            
            <hr/>
            <div>
            <ColocalizationSourcesSummary data={sourceSummaryData} showSourceTypes={true}/>
            </div>
            {
                selectedSources ? <div className="colocs-selection-dropdown">             
                <div className="dropdown-group">
                    <button className="dropdown-button" onClick={() => setShowDropdown(!showDropdown)}>{selectorText}
                        <div className="dropdown-pointer">
                            <i className="arrow down"></i>
                        </div>
                    </button>
                    <div className={ showDropdown ? "dropdown-content show" : "dropdown-content"}>
                        {inputCheckboxAllSources}
                        {
                            initialSources.map((key, i) => 
                                <div key={i} className="checkbox-item-div">
                                    <input type="checkbox" id={key} name={key} value={key} checked={selectedSources.indexOf(key) > -1}
                                        onChange={(e) => {
                                            var src = e.target.checked ? 
                                                [...selectedSources, e.target.value] : 
                                                selectedSources.filter(a => a !== e.target.value);
                                            setSelectedSources(src);
                                    }}/> 
                                    <span className="checkbox-label"><label htmlFor={key}>{key}</label></span>
                                </div>
                            )
                        }
                    </div>
                </div>
                </div> : null
            }

            <SelectTable data={ colocFiltBySource }
                         keyField="colocalization_id"
                         columns={ columns(listMetadata) }
                         defaultSorted={[{  id: "clpa", desc: true }]}
                         defaultPageSize={10}
                         filterable
                         defaultFilterMethod={(filter, row) => row[filter.id].toLowerCase().startsWith(filter.value.toLowerCase())}
                         SubComponent={ subComponent }
                         toggleSelection={toggleSelection}
                         selectType="radio"
                         isSelected={isSelected}
                         getTrProps={rowFn}
                         className="-striped -highlight"
                         useFlexLayout />
            <p></p>
            <div className="row">
                <div className="col-xs-12">
                    <CSVLink
                        headers={headers(listMetadata)}
                        data={ colocFiltBySource.map(flatten) }
                        separator={'\t'}
                        enclosingCharacter={''}
                        filename={`colocalization.tsv`}
                        className="btn btn-primary"
                        target="_blank">Download Table
                    </CSVLink>
                </div>

            </div>
        </div>);
    } else {
        return (<div>Loading ... </div>);
    }
}
export default ColocalizationList
