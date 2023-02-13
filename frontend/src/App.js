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
import { ListLoads } from "./component/listLoads";
import { ListFlows } from "./component/listFlow"; 
import { NewFlow } from "./component/newflow";
import { AuthContext } from "./context/AuthContext";
import { ListProjectFlows } from "./component/listProjectFlows";
import { Export } from "./component/export";
import { PerfMenu } from "./component/perfMenu"
import { FileMenu } from "./component/fileMenu";
import { ListCatalogs } from "./component/listCatalogs";
import { NewCatalog } from "./component/newCatalog";
import { ListRules } from "./component/listRules";
import { NewRule } from "./component/newRule";
import { ListPerf } from "./component/listPerf";
import { ListSummary } from "./component/listSummary";
import { ListLayouts } from "./component/listLayouts";
import { NewLayout } from "./component/newLayout";
import { ListPhonetics } from "./component/listPhonetics";
import { ListFrequency } from "./component/listFrequency";

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

              {/* FILE MENU LINKS */}
              <Route path="filemenu">
                <Route index element={<RequireAuth><FileMenu /></RequireAuth>} />
                <Route path='catalogs'>
                  <Route index element={<RequireAuth><ListCatalogs /></RequireAuth>} />
                  <Route path="new" 
                    element={
                    <RequireAuth>
                      <NewCatalog />
                    </RequireAuth>
                    }
                  />
                </Route>
                <Route path="rules/:project">
                  <Route index element={<RequireAuth><ListRules /></RequireAuth>} />
                  <Route path="new" 
                    element={
                    <RequireAuth>
                      <NewRule />
                    </RequireAuth>
                    }
                  />
                </Route>
                <Route path="layouts/:project">
                  <Route index element={<RequireAuth><ListLayouts /></RequireAuth>} />
                  <Route path="new" 
                    element={
                    <RequireAuth>
                      <NewLayout />
                    </RequireAuth>
                    }
                  />
                </Route>
              </Route>
              
              {/* DATAPERF LINKS */}
              <Route path="perfmenu">
                    <Route index element={<RequireAuth><PerfMenu /></RequireAuth>} />
                    <Route path="resume/:project">
                      <Route index element={<RequireAuth><ListPerf /></RequireAuth>} />
                    </Route>
                    <Route path="summary/:project">
                      <Route index element={<RequireAuth><ListSummary /></RequireAuth>} />
                    </Route>
                    <Route path="phonetics/:project">
                      <Route index element={<RequireAuth><ListPhonetics /></RequireAuth>} />
                    </Route>
                    <Route path="frequency/:project">
                      <Route index element={<RequireAuth><ListFrequency /></RequireAuth>} />
                    </Route>
              </Route>

              <Route 
                path="/dataloads" 
                element={
                <RequireAuth>
                  <ListLoads />
                </RequireAuth>
                }
              />
              <Route 
                path="/export" 
                element={
                <RequireAuth>
                  <Export />
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
                path="/projectflows" 
                element={
                  <RequireAuth>
                    <ListProjectFlows />
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
