import React from "react";
import "../general.scss";
import { DataSummaryTable } from "./dataSummaryTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListSummary = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <DataSummaryTable />
            </div>
        </div>
    )
}