import React from 'react'
import {Link} from 'react-router-dom'
import './Main.style.css'

const Main = () => {
  return (
    <div className='landing'>Landing Page 구현 전입니다. 감안하고 봐주세용 
    <p></p>
      <Link to='/prompt'> 
        <button>Start for Free</button>
        </Link>
    </div>
  )
}

export default Main;