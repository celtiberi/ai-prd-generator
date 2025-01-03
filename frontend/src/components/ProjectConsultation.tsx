import { useState } from 'react';
import { Box, VStack, Input, Button, Text, List, ListItem } from '@chakra-ui/react';
import { projectApi } from '../services/api';

export const ProjectConsultation: React.FC = () => {
    const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [summary, setSummary] = useState(null);

    const sendMessage = async () => {
        if (!currentMessage.trim()) return;
        
        try {
            const response = await projectApi.sendConsultationMessage(currentMessage);
            setMessages(prev => [...prev, 
                { role: 'user', content: currentMessage },
                { role: 'agent', content: response.message }
            ]);
            
            if (response.status === 'review_summary') {
                setSummary(response.summary);
            }
            
            setCurrentMessage('');
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    const approveSummary = async () => {
        try {
            const response = await projectApi.approveSummary();
            // Handle transition to LeadAgent phase
        } catch (error) {
            console.error('Error approving summary:', error);
        }
    };

    return (
        <Box>
            <VStack spacing={4}>
                {/* Display conversation history */}
                <List spacing={3} w="100%">
                    {messages.map((msg, idx) => (
                        <ListItem key={idx} 
                            bg={msg.role === 'user' ? 'blue.50' : 'gray.50'}
                            p={3} borderRadius="md">
                            {msg.content}
                        </ListItem>
                    ))}
                </List>

                {/* Show summary for review if available */}
                {summary && (
                    <Box p={4} borderWidth={1} borderRadius="md">
                        <Text fontWeight="bold">Project Summary</Text>
                        {/* Display summary details */}
                        <Button onClick={approveSummary}>
                            Approve Summary
                        </Button>
                    </Box>
                )}

                {/* Message input */}
                <Input
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Type your message..."
                />
                <Button onClick={sendMessage}>Send</Button>
            </VStack>
        </Box>
    );
}; 