import React from "react";
import Table from "./IndexTable";
import {setPageTitle} from "../../common/commonUtilities";

interface Props {}

const Index = (props : Props) =>   {
    const title : string = 'index';
    setPageTitle(title);

    return <Table/>;
}

export default Index;
