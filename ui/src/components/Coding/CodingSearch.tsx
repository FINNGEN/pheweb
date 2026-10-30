import React from 'react'
import AsyncSelect from 'react-select/async'
import { useHistory } from 'react-router-dom'
import { getAutocomplete } from "./CodingAPI";
import { AutoCompleteModel } from "./CodingModel";

const routeByType: { [type in AutoCompleteModel.Row['type']]: string } = {
    phenotype: 'phenocode',
    gene: 'gene',
    variant: 'variant',
}

const selectedPath = (selected: AutoCompleteModel.Row): string | null =>
    selected.type in routeByType ? `/coding/${routeByType[selected.type]}/${selected.value}` : null

/* only query the backend once the user has typed something, the full list is too large to load */
const loadOptions = (query: string, callBack) => {
    if (query.trim() === '') {
        callBack([])
    } else {
        getAutocomplete(query.trim(),
                        (results: AutoCompleteModel.Data) => callBack(results),
                        () => () => callBack([]))
    }
}

const customStyles = {
    container: provided => ({
        ...provided,
        width: 500,
        maxWidth: '90vw',
    }),
    control: provided => ({
        ...provided,
        width: 500,
        maxWidth: '90vw',
        height: 10
    }),
}
const Search = () => {
    const history = useHistory()
    const onChange = (selected) => {
        const path = selected && selectedPath(selected)
        if (path) {
            history.push(path)
        }
    }
    return (<form className="form-inline">
        <AsyncSelect
            placeholder={'Search by variant, gene, or phenotype'}
            onChange={onChange}
            loadOptions={loadOptions}
            menuPosition="fixed"
            styles={customStyles}
        />
    </form>)
}

export default Search