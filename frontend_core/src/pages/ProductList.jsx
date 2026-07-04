import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function ProductList() 
{
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => 
    {
        axios.get(`${import.meta.env.VITE_API_URL}/products/`)
            .then(response => {
                setProducts(response.data);
                setLoading(false);
            })
            .catch(error => {
                console.error("Error fetching products:", error);
                setLoading(false);
            });
    }, []);

    if (loading) return <h2 style={{ textAlign: 'center', marginTop: '50px' }}>Loading products...</h2>;
    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>Products Store</h1>
            
            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {products.map(product => (
                    <div key={product.id} style={{ 
                        border: '1px solid #ddd', 
                        padding: '20px', 
                        borderRadius: '8px',
                        width: '250px',
                        textAlign: 'center',
                        boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                    }}>
                        <h3>{product.name}</h3>
                        <p style={{ color: 'gray' }}>{product.description}</p>
                        <h2 style={{ color: '#2c3e50' }}>${product.base_price}</h2>
                        
                        <Link to={`/products/${product.id}`} style={{
                            display: 'inline-block',
                            marginTop: '15px',
                            padding: '10px 20px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            textDecoration: 'none',
                            borderRadius: '5px'
                        }}>
                            View Details
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ProductList;