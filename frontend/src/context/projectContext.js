import React, { createContext, useState, useEffect } from "react";

export const ProjectContext = createContext();

export const ProjectContextProvider = ({ children }) => {

    const [activeProject, setActiveProject] = useState(localStorage.getItem('project'));

    useEffect(() => {
        localStorage.setItem('project', activeProject);
    }, [activeProject]);

    return(
        <ProjectContext.Provider value={[activeProject, setActiveProject]}>
            {children}
        </ProjectContext.Provider>
    )
};