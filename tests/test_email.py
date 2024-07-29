import pytest
from unittest.mock import patch, AsyncMock
from pymasters.services.email import send_email
from pymasters.settings import conf

@pytest.mark.asyncio
async def test_send_email_success(test_user):
    email = test_user.email
    host = "http://localhost"
    
    with patch("pymasters.services.email.FastMail.send_message", new_callable=AsyncMock) as mock_send_message:
        mock_send_message.return_value = None  
        
        await send_email(email, host)
        
        mock_send_message.assert_called_once()
        args, kwargs = mock_send_message.call_args
        assert args[0].recipients == [email]
        assert args[0].template_body['host'] == host
        assert 'token' in args[0].template_body

@pytest.mark.asyncio
async def test_send_email_connection_error(test_user):
    email = test_user.email
    host = "http://localhost"
    
    with patch("pymasters.services.email.FastMail.send_message", new_callable=AsyncMock) as mock_send_message:
        mock_send_message.side_effect = Exception("Connection error")  
        
        with pytest.raises(Exception):
            await send_email(email, host)
            
        mock_send_message.assert_called_once()

