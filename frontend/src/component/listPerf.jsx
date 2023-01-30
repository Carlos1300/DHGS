import React from "react";
import "../general.scss";
import { DataPerfTable } from "./dataPerfTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListPerf = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <DataPerfTable />
            </div>
        </div>
    )
}