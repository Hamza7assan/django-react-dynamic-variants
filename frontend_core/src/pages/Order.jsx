import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

function Order() {
    const location = useLocation();
    const navigate = useNavigate();
    
    const { productName, comboId, price, maxStock } = location.state || {};
    
    const [quantity, setQuantity] = useState(1);
    const [statusMsg, setStatusMsg] = useState(null);
    const [isSuccess, setIsSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    if (!comboId) {
        navigate('/products');
        return null;
    }

    const totalPrice = (parseFloat(price) * quantity).toFixed(2);

    const handlePlaceOrder = () => {
        setLoading(true);
        setStatusMsg(null);

        axios.post(`${import.meta.env?.VITE_API_URL || 'http://localhost:8000'}/orders/`, {
            combination_id: comboId,
            quantity: quantity
        })
        .then(res => {
            setIsSuccess(true);
            setStatusMsg(`Order confirmed successfully! Order ID: ${res.data.order_id}`);
            setLoading(false);
        })
        .catch(err => {
            setIsSuccess(false);
            setStatusMsg(err.response?.data?.error || 'An error occurred during ordering');
            setLoading(false);
        });
    };

    return (
        <div style={{ maxWidth: '600px', margin: '50px auto', padding: '30px', border: '1px solid #ddd', borderRadius: '10px', textAlign: 'center' }}>
            <h2>Checkout</h2>
            <hr style={{ margin: '20px 0' }} />
            
            <h3>Product: {productName}</h3>
            <p style={{ fontSize: '18px', color: 'gray' }}>Price per unit: ${price}</p>
            
            <div style={{ margin: '30px 0' }}>
                <label style={{ fontSize: '18px', marginRight: '10px' }}>Quantity:</label>
                <input 
                    type="number" 
                    min="1" 
                    max={maxStock} 
                    value={quantity} 
                    onChange={(e) => setQuantity(parseInt(e.target.value))}
                    disabled={isSuccess}
                    style={{ padding: '10px', fontSize: '16px', width: '80px', textAlign: 'center' }}
                />
                <p style={{ color: 'blue', fontSize: '14px', marginTop: '10px' }}>Max available: {maxStock}</p>
            </div>
            <h2 style={{ color: 'green' }}>Total: ${totalPrice}</h2>
            {statusMsg && (
                <div style={{ padding: '15px', marginTop: '20px', backgroundColor: isSuccess ? '#d4edda' : '#f8d7da', color: isSuccess ? '#155724' : '#721c24', borderRadius: '5px' }}>
                    {statusMsg}
                </div>
            )}
            {!isSuccess && (
                <button 
                    onClick={handlePlaceOrder}
                    disabled={loading || quantity < 1 || quantity > maxStock}
                    style={{
                        width: '100%', padding: '15px', marginTop: '20px', fontSize: '18px',
                        backgroundColor: (loading || quantity < 1 || quantity > maxStock) ? '#ccc' : '#007bff',
                        color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'
                    }}
                >
                    {loading ? 'Processing...' : 'Confirm Order'}
                </button>
            )}
            {isSuccess && (
                <button 
                    onClick={() => navigate('/products')}
                    style={{ width: '100%', padding: '15px', marginTop: '20px', fontSize: '18px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
                >
                    Back to Store
                </button>
            )}
        </div>
    );
}

export default Order;