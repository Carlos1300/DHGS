import React, { createContext, useState } from "react";

export const ProjectContext = createContext();

export const ProjectContextProvider = ({ children }) => {

    const [activeProject, setActiveProject] = useState('None');

    return(
        <ProjectContext.Provider value={[activeProject, setActiveProject]}>
            {children}
        </ProjectContext.Provider>
    )
};