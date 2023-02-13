import React from "react";
import "../general.scss";
import { PhoneticsTable } from "./phoneticsTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListPhonetics = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <PhoneticsTable />
            </div>
        </div>
    )
}