import React from "react";
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {About} from './component/about';
import { Dashboard } from "./component/dashboard";
import {Users} from './component/users';
// import {Navbar} from './component/navbar';
import {Login} from './component/login';

function App() {
  return (
      <Router>
          <Routes>
            <Route path="/users" element={<Users />}/>
            <Route path="/about" element={<About />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/" element={<Login />} />
          </Routes>
      </Router>
  );
}

export default App;
