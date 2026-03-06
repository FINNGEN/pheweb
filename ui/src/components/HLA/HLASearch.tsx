import React from 'react'
import Select from 'react-select'
import { getAutocomplete } from "./HLAAPI";
import { SearchResult } from "./HLAModel";


const onChange = (selected) => {
    const value: SearchResult = selected.value
    let url = `/error/${selected.display}`
    if ('phenocode' in value) {
        url = `/hla/phenocode/${selected.label}`
    }
    else if ('gene' in value) {
        url = `/hla/gene/${selected.label}`
    }
    else if ('alt' in value) {
        url = `/hla/variant/${selected.label}`
    }
    window.location.href = url
}

const reshapeResult = (result: SearchResult) => {
    if ('phenocode' in result) {
        return { value: result, label: result.phenocode }
    }
    else if ('gene' in result) {
        return { value: result, label: result.gene }
    }
    else if ('alt' in result) {
        return { value: result, label: result.alt }
    }
    return result
}

const customStyles = {
    container: provided => ({
        ...provided,
        width: 500
    }),
    control: provided => ({
        ...provided,
        width: 500,
        height: 10
    }),
}
const Search = () => {
    const [autoCompleteOptions, setOptions] = React.useState<{ value: SearchResult, label: string }[]>([])
    React.useEffect(
        () => {
            getAutocomplete((results: SearchResult[]) => setOptions(results.map(reshapeResult)))
        },
        []
    )
    return (<form className="form-inline">
        <Select
            placeholder={'Show all HLA results for a variant, gene, or phenotype'}
            onChange={onChange}
            options={autoCompleteOptions}
            menuPosition="fixed"
            styles={customStyles}
        />
    </form>)
}

export default Search
