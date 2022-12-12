import React from "react";
import "../general.scss";
import { DataLoadsTable } from "./dataLoadsTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListLoads = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <DataLoadsTable />
            </div>
        </div>
    )
}