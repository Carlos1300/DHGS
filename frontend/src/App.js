import React from "react";
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
// import {About} from './component/about';
import { Dashboard } from "./component/dashboard";
// import {Users} from './component/users';
// import {Navbar} from './component/navbar';
import {Login} from './component/login';
import { List } from "./component/list";
import { Single } from "./component/single";
import { New } from "./component/new";

function App() {
  return (
      <Router>
          <Routes>
            <Route path="/"/>
              <Route index element={<Login />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/repo" element={<List />}/>
              <Route path="/cuenta" element={<Single />}/>
              <Route path="/nuevo" element={<New />}/>
          </Routes>
      </Router>
  );
}

export default App;
