import PriceTicker from '../components/PriceTicker'

function Home(){
    return(
        <div className="p-8">
            <h1 className="text-2xl font-bold mb-4">CryptoPulse</h1>
            <PriceTicker />
        </div>
    )
}

export default Home

