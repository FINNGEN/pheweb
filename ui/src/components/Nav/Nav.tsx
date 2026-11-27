import React, { useState } from 'react'
import { ConfigurationWindow } from '../../components/Configuration/configurationModel'
import { mustacheSpan } from '../../common/commonUtilities'
import Search from './Search'
import Logout from './Logout'

declare let window: ConfigurationWindow
const application = window?.config?.application
const userInterface = window?.config?.userInterface

export const navLink = (href : string, label : string) => <li className="nav-item">
  <a className="nav-link" href={href} style={{ color: '#333', fontWeight: 'bold' }}>{label}</a>
</li>
const show = <X,>(toogle : boolean) => (value :X) => toogle?value:<></>

const Nav = () => {

  const logo = mustacheSpan(application?.logo || 'LOGO',{}) // mustacheSpan('', {});
  const title = application?.title || 'TITLE'
  const hasLOF = userInterface?.lof !== undefined,
    hasCoding = userInterface?.coding !== undefined,
    hasChip = userInterface?.chip !== undefined,
    hasHLA = userInterface?.hla !== undefined,
    hasAbout = userInterface?.about !== undefined;
  // the collapsed menu on narrow screens, bootstrap shows it with the show class
  const [expanded, setExpanded] = useState(false);

  // px-3: bootstrap 5 dropped the navbar's own horizontal padding
  return <nav className="navbar navbar-expand-lg navbar-light nav-bg px-3">
    <a className="navbar-brand" href="/">{ logo }</a>
    <a className="navbar-brand" href="/"> <span className='logo-header'>{ title }</span></a>
    <button className="navbar-toggler" type="button" onClick={() => setExpanded(!expanded)}
            aria-controls="navbarColor01" aria-expanded={expanded} aria-label="Toggle navigation">
      <span className="navbar-toggler-icon"></span>
    </button>

    <div className={`collapse navbar-collapse${expanded ? ' show' : ''}`} id="navbarColor01">
      <Search/>
      <ul className="navbar-nav ms-auto">
        {show(hasLOF)(navLink('/lof','LOF'))}
        {show(hasCoding)(navLink('/coding','Coding'))}
        {show(hasHLA)(navLink('/hla/top','HLA'))}
        {show(hasChip)(navLink('/chip','Chip'))}
        {show(hasAbout)(navLink('/about','About'))}
        <Logout/>
      </ul>
    </div>
  </nav>
}

export default Nav
