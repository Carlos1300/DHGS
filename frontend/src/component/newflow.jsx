import React, { useState, useEffect } from "react";
import "../general.scss";
import { Navbar } from "./navbar";
import { Sidebar } from "./sidebar";
import Swal from 'sweetalert2';
import { useNavigate } from "react-router-dom";
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';
import Modal from '@mui/material/Modal';
import Backdrop from '@mui/material/Backdrop';
import Fade from '@mui/material/Fade';

const API = process.env.REACT_APP_API;

export const NewFlow = () =>{

    const [rulesList, setRulesList] = useState([]);
    const [rulesNames, setRulesNames] = useState([]);
    const [paramsList, setParamsList] = useState([]);
    const [page, setPage] = useState(0);
    const [availableRules, setAvailableRules] = useState([]);
    const [flowName, setFlowName] = useState("");
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);
    const [modalRule, setModalRule] = useState('');
    const [openRuleModal, setOpenRuleModal] = useState(false);
    const [openParamModal, setOpenParamModal] = useState(false);

    const handleOpen = (item) => {
        setOpen(true);
        setModalRule(item);
    }
    const handleClose = () => setOpen(false);

    const handleRuleOpen = () => setOpenRuleModal(true);

    const handleRuleClose = () => setOpenRuleModal(false);

    const handleParamOpen = () => setOpenParamModal(true);

    const handleParamClose = () => setOpenParamModal(false);

    const getRules = async () =>{
        const res = await fetch(API + '/getRules');
        const data = await res.json();
        setAvailableRules(data);
      }
    
      useEffect(() => {
        getRules();
      }, [])

    const extractParams = () => {

        const extractedParams = [];
        const paramJSON = {};

        for ( let i=0 ; i < availableRules.length ; i++) {
            if (rulesList.includes(availableRules[i].value)){
                paramJSON.name = availableRules[i].name;
                paramJSON.params = availableRules[i].params
                extractedParams.push({...paramJSON})
            }
        }

        return extractedParams;
    }

    // const extractedParams = extractParams();

    const handleChange = (e) =>{
        const {value, checked} = e.target;
        const rulename = e.target.name

        if(checked){
            setRulesList(pre => [...pre, value]);
            setRulesNames(pre => [...pre, rulename])
        }else{
            setRulesList(pre => {
                return [...pre.filter(rule => rule !== value)];
            })
            setRulesNames(pre => {
                return [...pre.filter(name => name!== rulename)];
            })
        }
    }

    const handleParamChange = (e) => {
        if (e.target.type === 'file'){
            let updatedValue = {}
            updatedValue = {[e.target.name]: e.target.files[0]}

            setParamsList(paramsList => ({
                ...paramsList,
                ...updatedValue
                
            }))
        } else {
            let updatedValue = {}
            updatedValue = {[e.target.name]: e.target.value}

            setParamsList(paramsList => ({
                ...paramsList,
                ...updatedValue
                
            }))
        }
    }

    const handleSubmit = async (e) => {

        e.preventDefault();

        const JSONdata = [];

        JSONdata.push({...{
            flowName: flowName
        }});

        let JSONelement = {};

        JSONdata.push({...{
            dispname: "Cargar fuente",
            order: 0,
            name: "load_source_main"
        }})

        let order = 1;

        if(rulesList.length !== 0 && paramsList.length !== 0){ 
            for (const rule of availableRules.map(a => a)){
                if (rulesList.includes(rule.value)){
                    JSONelement.dispname = rule.name
                    JSONelement.name = rule.value
                    JSONelement.order = order;
                    order++;
                    for(const param of rule.params.map(a => a.name)){
                        JSONelement[param] = paramsList[param];
                    }

                    JSONdata.push({...JSONelement})
                }

                for (const prop of Object.getOwnPropertyNames(JSONelement)) {
                    delete JSONelement[prop];
                }
            }
        } else{
            for (const rule of availableRules.map(a => a)){
                if (rulesList.includes(rule.value)){
                    JSONelement.dispname = rule.name
                    JSONelement.name = rule.value
                    JSONelement.order = order;
                    order++;

                    JSONdata.push({...JSONelement})
                }

                for (const prop of Object.getOwnPropertyNames(JSONelement)) {
                    delete JSONelement[prop];
                }
            }
        }

        JSONdata.push({...{
            dispname: "Guardar Datos",
            order: order++,
            name: "save_source_main",
            collection: "DataCleaned"
        }})
            
        const res = await fetch(API + '/my_flows/' + localStorage.getItem('email'),{
            method: 'POST',
            headers:{
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(JSONdata),
        });

        const data = await res.json();

        if(res.status !== 200 && data.msg !== ''){
            Swal.fire({
                title: 'Error al cargar la fuente de datos',
                text: 'Revise de nuevo los campos.',
                icon: 'error',
                button: 'Volver a intentarlo',
                confirmButtonColor: "#000",
                timer: "10000"
            });

            setRulesList([]);
            setParamsList([]);

        }else{
            Swal.fire({
                title: 'Carga exitosa',
                text: data.msg,
                icon: 'success',
                button: 'Continuar',
                confirmButtonColor: "#000",
                timer: "10000"
            })

            navigate('/flows')
            setRulesList([]);
            setParamsList([]);
        }
        
    }

    const titles = ['Agregar Reglas', 'Agregar Parámetros'];
    const handlers = [handleRuleOpen, handleParamOpen];

    const forwardButton = () =>{
        setPage((page) => page + 1);
        extractParams();

    }

    const returnButton = () =>{
        setRulesList((rulesList) => rulesList.splice(0, rulesList.length));
        setRulesNames((rulesNames) => rulesNames.splice(0, rulesNames.length));
        setPage((page) => page - 1);
    }

    return(
        <div className="new">
            <Sidebar />
            <div className="newContainer">
                <Navbar />
                <Modal open={open} onClose={handleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
                    <Fade in={open}>
                        <div className="modalBox">
                        <div className="closeBtn" onClick={handleClose}>&times;</div>
                        <div className="modalContent">
                            <div className="modalTitle">
                                <h3><b>{modalRule.name}</b></h3>
                            </div>
                            <div className="modalText">
                            <p>{modalRule.modalDesc}</p>
                            <p>A continuación, se presenta un desglose de los parámetros de la regla.</p>
                            <div className="modalTable">
                                <table>
                                <thead>
                                    <tr>
                                        <th style={{width: "30%"}}>Parámetro</th>
                                        <th style={{width: "70%"}}>Descripción</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {
                                        modalRule !== '' ? (
                                            modalRule.params.map((item, index) => (
                                                <tr key={index}>
                                                    <td>{item.display_name !== 'None' ? item.display_name : 'Ninguno'}</td>
                                                    <td>{item.modalDesc !== 'None' ? item.modalDesc : 'No hay descripción.'}</td>
                                                </tr>
                                            ))
                                        ) : (
                                            <></>
                                        )
                                    }
                                </tbody>
                                </table>
                            </div>
                            <br />
                            <p><b>Resultado: </b>{modalRule.result}</p>
                            </div>
                        </div>
                        </div>
                    </Fade>
                </Modal>

                <Modal open={openRuleModal} onClose={handleRuleClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
                    <Fade in={openRuleModal}>
                    <div className="modalBox">
                        <div className="closeBtn" onClick={handleRuleClose}>&times;</div>
                        <div className="modalContent">
                        <div className="modalTitle">
                            <h3><b>Selección de Reglas</b></h3>
                        </div>
                        <div className="modalText">
                            <p>En esta página podrás elegir aquellas reglas que conformarán el nuevo flujo a añadir, así como darle un nombre a tu flujo para así identificarlo.</p>
                            <p>Para conocer los detalles de cada una de las reglas puedes dar click en el botón de color verde con el ícono <QuestionMarkIcon style={{fontSize: "16px"}} />, al hacerlo podrás consultar la información técnica de la regla.</p>
                            <p>Al añadir una regla al flujo podrás observar que la sección con el nombre <i>Orden de Reglas</i> se actualizará y te indicará el orden en el que serán ejecutadas las reglas del flujo.</p>
                            <p>Al finalizar de añadir reglas, da click en al botón <i>Siguiente</i> que te llevará a la sección donde podrás parametrizar las reglas que has seleccionado.</p>
                        </div>
                        </div>
                    </div>
                    </Fade>
                </Modal>

                <Modal open={openParamModal} onClose={handleParamClose} closeAfterTransition BackdropComponent={Backdrop} BackdropProps={{timeout: 500,}}>
                    <Fade in={openParamModal}>
                    <div className="modalBox">
                        <div className="closeBtn" onClick={handleParamClose}>&times;</div>
                        <div className="modalContent">
                        <div className="modalTitle">
                            <h3><b>Parametrización</b></h3>
                        </div>
                        <div className="modalText">
                            <p>En esta página podrás añadir los parámetros necesarios a las reglas que has seleccionado. Se recomienda que tengas a la mano tu fuente de datos y que previamente hayas dado de alta cualquier archivo que necesites para que el proceso de parametrización sea más sencillo y también para asegurar el buen funcionamiento del flujo que será añadido</p>
                            <p>Al finalizar la parametrización de las reglas da click en el botón <i>Añadir</i> para agregar el flujo al DataHub.</p>
                        </div>
                        </div>
                    </div>
                    </Fade>
                </Modal>

                <div className="top">
                    <h1 className="title">{titles[page]}</h1>
                    <button className="helpButton" onClick={handlers[page]}><QuestionMarkIcon /></button>
                </div>
                <div className={ page !== 0 ? "top flowname none" : "top flowname"}>
                    <p className="ruletitle">Nombre</p>
                    <input className="parambox" type="text" name="flowName" value={flowName} onChange={e => setFlowName(e.target.value)} required placeholder="Nombre del Flujo" />
                </div>
                <div className="top flowname">
                    <p className="ruletitle">Orden de reglas</p>
                    {
                        rulesNames.length === 0 ? (
                            <p style={{textAlign: 'center'}}>¡No se ha seleccionado ninguna regla!</p>
                        ) : (
                            <p>
                                {
                                    rulesNames.map((item, index) => (
                                        <span key={index}>{index === rulesNames.length-1 ? item : item + ' ' + String.fromCharCode(8594) + ' '}</span>
                                    ))
                                }
                            </p>
                        )
                    }
                </div>

                {
                    page === 0 ? (

                        <div className="bottom flow">
                            {
                                availableRules.map((item, index) => (
                                    <div className="col" key={index}>
                                        <input type="checkbox" value={item.value} onChange={handleChange} name={item.name} /> <span className="ruletitle">{item.name} <button onClick={() => handleOpen(item)}><QuestionMarkIcon className="icon" /></button></span>
                                        <p className="ruledesc">{item.desc}</p>
                                    </div>
                                ))
                            }
                        </div>
                    ) : (
                                <>
                                {
                                    extractParams().length !== 0 ? (

                                        extractParams().map((item, index) => {
                                            return(
                                                <div key={index} className="bottom flow">
                                            {item.params.map((param, index) => {
                                                return(
                                                param.name !== 'None' ? (
                                                    <div className="col parameters" key={index}>
                                                        <p className={index === 0 ? 'ruletitle' : 'ruletitle none'}>{item.name}</p>
                                                        <p className="displayName" key={index}>{param.display_name}</p>
                                                        <input className="parambox" placeholder={param.desc} onChange={handleParamChange} name={param.name} type={param.type} required/>
                                                    </div>
                                                ) : (
                                                    <div className="col parameters" key={index}>
                                                        <p className="ruletitle">{item.name}</p>
                                                        <p className="noParams">Esta regla no cuenta con parámetros.</p>
                                                        <hr></hr>
                                                    </div>
                                                )
                                            )})}
                                            </div>
                                        )})
                                        
                                    ) : (
                                        <div className="bottom flow">
                                            <div className="col warn" style={{justifyContent: "center"}}>
                                                <p className="warning">¡Ninguna regla seleccionada!</p>
                                            </div>
                                        </div>
                                    )

                                }
                        </>
                    )
                }

                {page === 0 ? (
                    <div className="changebuttons">
                        <button onClick={forwardButton}>Siguiente</button>
                    </div>

                ):(
                    <div className="changebuttons second">
                        <button onClick={returnButton}>Anterior</button>
                        <button disabled={extractParams().length === 0} onClick={handleSubmit}>Añadir</button>
                    </div>

                )}
            </div>
        </div>
    )
}