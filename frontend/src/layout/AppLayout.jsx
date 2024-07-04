import {Link, Outlet} from 'react-router-dom'
import logo from '../logo.png'
import {Container, Nav, Navbar} from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

const AppLayout = () => {
  
    return(
    <div> 
    <Navbar collapseOnSelect expand="lg" style = {{width: '100%', margin: '0 auto'}} className="bg-white">
        <Container>
            <Navbar.Brand> 
                <Link to='/'>
                    <img class='bar-logo' src={logo} width={150}/>
                </Link>
            </Navbar.Brand>
        </Container>
        </Navbar>
        <hr style={{ width: '85%', margin: '0 auto', marginTop: '-15px', marginBottom: '20px', height: '1px', color:'#1A67F8', opacity:0.9 }} />
        <div style={{width: '100%', margin: '0 auto'}}>
            <Outlet />
        </div>
    </div>
    )
};

export default AppLayout;