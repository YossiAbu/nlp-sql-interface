import { useNavigate } from "react-router-dom";
import heroBackground from "../assets/hero-background.jpg";


const Home = () => {
  const navigate = useNavigate()

  return (
    <div className="w-full h-screen">
      <div 
        className="w-full h-full relative bg-gradient-hero flex items-center justify-center text-center overflow-hidden"
        style={{
          backgroundImage: `url(${heroBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div>
          <h1 className="text-cyan-400 text-4xl font-bold mb-6">
            Ask Your Database<br />Anything
          </h1>
          <button className="mt-6" onClick={() => navigate('/')}>
            stam
          </button>
        </div>
      </div>
    </div>
  )
}


export default Home;