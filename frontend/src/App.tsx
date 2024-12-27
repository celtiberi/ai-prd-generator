import React from 'react';
import { ChakraProvider, Box, VStack } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ProjectForm } from './components/ProjectForm';
import { ProgressView } from './components/ProgressView';
import { useProjectStore } from './store';

const queryClient = new QueryClient();

export const App: React.FC = () => {
    const { project } = useProjectStore();

    return (
        <QueryClientProvider client={queryClient}>
            <ChakraProvider>
                <Box p={8}>
                    <VStack spacing={8} align="stretch">
                        {!project ? (
                            <ProjectForm />
                        ) : (
                            <ProgressView />
                        )}
                    </VStack>
                </Box>
            </ChakraProvider>
        </QueryClientProvider>
    );
}; 