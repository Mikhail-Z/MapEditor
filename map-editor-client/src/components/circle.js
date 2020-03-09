import {React} from 'react'
import PropTypes from 'prop-types'

const Circle = ({color}) => 
    <div className="circle" style={{backgroundColor: color}}>test</div>



Circle.propTypes = {
    color: PropTypes.string.isRequired
}

export default Circle