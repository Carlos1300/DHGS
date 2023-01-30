import React from "react";
import "../general.scss";
import { LayoutsTable } from "./layoutsTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListLayouts = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <LayoutsTable />
            </div>
        </div>
    )
}