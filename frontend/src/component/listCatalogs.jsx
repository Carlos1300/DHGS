import React from "react";
import "../general.scss";
import { CatalogsTable } from "./catalogsTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListCatalogs = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <CatalogsTable />
            </div>
        </div>
    )
}