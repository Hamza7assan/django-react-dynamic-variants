import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000';

function ProductDetail() {
    const { id } = useParams(); 
    const navigate = useNavigate();
    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selections, setSelections] = useState({});
    const [comboResult, setComboResult] = useState(null);
    const [errorMsg, setErrorMsg] = useState('');

    useEffect(() => {
        if (!id) {
            setLoading(false);
            return;
        }

        axios.get(`${API_URL}/products/${id}/`)
            .then(res => {
                setProduct(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setErrorMsg('Failed to load product data');
                setLoading(false);
            });
    }, [id]);

    useEffect(() => {
        if (!product) return;

        // Edge Case 1: Handle simple products without variant types (e.g., Mug)
        if (product.variant_types && product.variant_types.length === 0) {
             axios.post(`${API_URL}/products/${id}/combinations/lookup/`, { option_ids: [] })
                .then(res => {
                    setComboResult(res.data); 
                    setErrorMsg('');
                })
                .catch(err => {
                    setComboResult(null);
                    setErrorMsg('Product is currently unavailable');
                });
             return;
        }

        // Edge Case 2: Handle complex products with variants
        if (product.variant_types && product.variant_types.length > 0) {
            // Check if user has selected an option for every variant type
            const isFullySelected = Object.keys(selections).length === product.variant_types.length;

            if (isFullySelected) {
                const option_ids = Object.values(selections);
                
                axios.post(`${API_URL}/products/${id}/combinations/lookup/`, { option_ids })
                    .then(res => {
                        setComboResult(res.data); 
                        setErrorMsg('');
                    })
                    .catch(err => {
                        setComboResult(null);
                        setErrorMsg('This combination is currently unavailable');
                    });
            } else {
                setComboResult(null); 
            }
        }
    }, [selections, product, id]);

    const handleSelect = (variantId, optionId) => {
        setSelections(prev => ({
            ...prev,
            [variantId]: optionId
        }));
    };

    if (loading) return <h2 style={{ textAlign: 'center', marginTop: '50px' }}>Loading...</h2>;
    if (!product) return <h2 style={{ textAlign: 'center', color: 'red' }}>Product not found</h2>;

    return (
        <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px' }}>
            <h1>{product.name}</h1>
            <p style={{ color: 'gray' }}>{product.description}</p>
            
            {!comboResult && <h2>Base Price: ${product.base_price}</h2>}

            <hr style={{ margin: '20px 0' }} />

            {product.variant_types && product.variant_types.map(vt => (
                <div key={vt.id} style={{ marginBottom: '20px' }}>
                    <h3 style={{ marginBottom: '10px' }}>Select {vt.name}:</h3>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        {vt.options.map(opt => (
                            <button
                                key={opt.id}
                                onClick={() => handleSelect(vt.id, opt.id)}
                                style={{
                                    padding: '10px 20px',
                                    border: selections[vt.id] === opt.id ? '2px solid #007bff' : '1px solid #ccc',
                                    backgroundColor: selections[vt.id] === opt.id ? '#e7f1ff' : '#fff',
                                    cursor: 'pointer',
                                    borderRadius: '5px',
                                    fontWeight: selections[vt.id] === opt.id ? 'bold' : 'normal'
                                }}
                            >
                                {opt.value}
                            </button>
                        ))}
                    </div>
                </div>
            ))}

            <hr style={{ margin: '20px 0' }} />

            <div style={{ minHeight: '100px' }}>
                {errorMsg && <p style={{ color: 'red', fontWeight: 'bold' }}>{errorMsg}</p>}
                
                {comboResult && (
                    <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '5px' }}>
                        <h2 style={{ color: 'green' }}>Final Price: ${comboResult.final_price}</h2>
                        {comboResult.in_stock ? (
                            <p style={{ color: 'blue', fontWeight: 'bold' }}>
                                In Stock: {comboResult.stock} pieces
                            </p>
                        ) : (
                            <p style={{ color: 'red', fontWeight: 'bold' }}>Out of Stock</p>
                        )}
                    </div>
                )}
            </div>

            <button 
                onClick={() => navigate('/order', { 
                    state: { 
                        productName: product.name,
                        comboId: comboResult.combination_id,
                        price: comboResult.final_price,
                        maxStock: comboResult.stock
                    } 
                })}
                disabled={!comboResult || !comboResult.in_stock}
                style={{
                    width: '100%',
                    padding: '15px',
                    fontSize: '18px',
                    backgroundColor: comboResult?.in_stock ? '#28a745' : '#ccc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '5px',
                    cursor: comboResult?.in_stock ? 'pointer' : 'not-allowed',
                    marginTop: '20px'
                }}
            >
                {comboResult?.in_stock ? 'Add to Cart (Buy)' : 'Please complete your selections'}
            </button>
        </div>
    );
}

export default ProductDetail;