import React from "react";
import "../general.scss";
import { DataTable } from "./dataTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const List = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <DataTable />
            </div>
        </div>
    )
}