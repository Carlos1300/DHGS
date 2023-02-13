import React from "react";
import "../general.scss";
import { FrequencyTable } from "./frequencyTable";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";

export const ListFrequency = () =>{
    return(
        <div className="list">
            <Sidebar />
            <div className="listContainer">
                <Navbar />
                <FrequencyTable />
            </div>
        </div>
    )
}