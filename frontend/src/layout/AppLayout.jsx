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
                    <img src={logo} width={150}/>
                </Link>
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className='ms-auto'>
                <Nav.Link style={{color:'#102A56', marginRight:'15px'}}>Guide</Nav.Link>
                <Nav.Link style={{color:'#102A56', marginRight:'15px'}}> Features</Nav.Link>
                <Nav.Link>
                    <Link to='/prompt' style={{color:'#102A56', textDecoration:'none'}}>
                        Try it
                    </Link>
                </Nav.Link>
            </Nav>
            </Navbar.Collapse>
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