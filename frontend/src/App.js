import React, { useContext } from "react";
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
// import {About} from './component/about';
import { Dashboard } from "./component/dashboard";
// import {Users} from './component/users';
// import {Navbar} from './component/navbar';
import { Login } from './component/login';
import { List } from "./component/list";
import { Single } from "./component/single";
import { New } from "./component/new";
import { ListPerf } from "./component/listPerf";
import { ListLoads } from "./component/listLoads";
import { ListFlows } from "./component/listFlow"; 
import { NewFlow } from "./component/newflow";
import { AuthContext } from "./context/AuthContext";

function App() {

  const {currentUser} = useContext(AuthContext);

  const RequireAuth = ({ children }) => {
    if(currentUser === null || currentUser === 'null'){
      return <Navigate to= '/' />
    } else{
      return children
    }
  }

  return (
      <Router>
          <Routes>
            <Route path="/"/>
              <Route index element={<Login />} />
              <Route 
                path="/dashboard" 
                element={
                  <RequireAuth>
                    <Dashboard />
                  </RequireAuth>
                } 
              />
              <Route 
                path="/repo" 
                element={
                <RequireAuth>
                  <List />
                </RequireAuth>
                }
              />
              <Route 
                path="/dataperf" 
                element={
                <RequireAuth>
                  <ListPerf />
                </RequireAuth>
                }
              />
              <Route 
                path="/dataloads" 
                element={
                <RequireAuth>
                  <ListLoads />
                </RequireAuth>
                }
              />
              <Route 
                path="/flows" 
                element={
                  <RequireAuth>
                    <ListFlows />
                  </RequireAuth>
                }
              />
              <Route 
                path="/cuenta" 
                element={
                  <RequireAuth>
                    <Single />
                  </RequireAuth>
                }
              />
              <Route 
                path="/nuevo" 
                element={
                <RequireAuth>
                  <New />
                </RequireAuth>
                }
              />
              <Route 
                path="/nuevoflujo" 
                element={
                  <RequireAuth>
                    <NewFlow />
                  </RequireAuth>
                }
              />
          </Routes>
      </Router>
  );
}

export default App;
