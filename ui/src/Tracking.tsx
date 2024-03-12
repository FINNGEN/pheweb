import React, { useEffect } from "react";
import { ConfigurationWindow } from './components/Configuration/configurationModel';
import TagManager from 'react-gtm-module'

const gtmId : string | null | undefined = window?.config?.application?.trackingId;

declare let window: ConfigurationWindow;


const trackPageView = () : void => {
  if (typeof gtmId === "string") {
    const tagManagerArgs = { gtmId };
    TagManager.initialize(tagManagerArgs)
  }
}

interface Props {}

const Tracking = (props : Props) => {
      useEffect(trackPageView, []);
      return <div className="hidden"></div>
}

export default Tracking;
