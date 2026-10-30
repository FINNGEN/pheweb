import React, { useState } from 'react'
import { Link, useHistory } from 'react-router-dom'

const variantPattern = /^(chr)?([0-9]{1,2}|X|Y|MT?)[-:_]([0-9]+)[-:_]([ACGT]+)[-:_]([ACGT]+)$/i

/**
 * Parse a search query into a variant (chr-pos-ref-alt with 23 as X) or a gene.
 */
export const parseQuery = (query: string): { variant?: string, gene?: string } => {
    const match = query.trim().match(variantPattern)
    if (match) {
        const chrom = match[2].toUpperCase() === '23' ? 'X' : match[2].toUpperCase()
        return { variant: [chrom, match[3], match[4].toUpperCase(), match[5].toUpperCase()].join('-') }
    }
    return { gene: query.trim().toUpperCase() }
}

export const queryToPath = (query: string): string => {
    const { variant, gene } = parseQuery(query)
    return variant ? `/coding/variant/${variant}` : `/coding/gene/${gene}`
}

const Search = ({ isTop }: { isTop: boolean }) => {
    const [value, setValue] = useState('')
    const history = useHistory()
    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (value.trim() !== '') {
            history.push(queryToPath(value))
        }
    }
    return (<div className="search">
        <form className="form-inline" onSubmit={onSubmit}>
            <input
                style={{ width: '30ch' }}
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="search by gene or chr-pos-ref-alt"
            />
            <input type="submit" value="go" />
        </form>
        <span style={{ padding: '20px' }}>or</span>
        {isTop ? <span className="disabled">show top results</span> : <Link to="/coding">show top results</Link>}
    </div>)
}

export default Search
