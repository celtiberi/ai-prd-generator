import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Box, VStack, FormControl, FormLabel, Input, Textarea, Button, Text, List, ListItem, IconButton } from '@chakra-ui/react';
import { Project, ProjectInitResponse } from '../types';
import { projectApi } from '../services/api';
import { useProjectStore } from '../store';

export const ProjectForm: React.FC = () => {
    const { register, handleSubmit } = useForm<Project>();
    const [proposedObjectives, setProposedObjectives] = useState<string[]>([]);
    const [showObjectives, setShowObjectives] = useState(false);
    const setProject = useProjectStore((state) => state.setProject);

    const onSubmit = async (data: Project) => {
        try {
            const result = await projectApi.initialize(data);
            if (result.status === 'awaiting_objective_approval') {
                setProposedObjectives(result.proposed_objectives);
                setShowObjectives(true);
            }
        } catch (error) {
            console.error('Error initializing project:', error);
        }
    };

    const handleObjectiveApproval = async () => {
        try {
            const result = await projectApi.approveObjectives({ objectives: proposedObjectives });
            if (result.status === 'research_started') {
                setProject({ ...result.project });
            }
        } catch (error) {
            console.error('Error approving objectives:', error);
        }
    };

    return (
        <Box>
            {!showObjectives ? (
                <Box as="form" onSubmit={handleSubmit(onSubmit)}>
                    <VStack spacing={4}>
                        <FormControl isRequired>
                            <FormLabel>Project Title</FormLabel>
                            <Input {...register('title')} />
                        </FormControl>

                        <FormControl isRequired>
                            <FormLabel>Description</FormLabel>
                            <Textarea {...register('description')} />
                        </FormControl>

                        <FormControl isRequired>
                            <FormLabel>Target Users (one per line)</FormLabel>
                            <Textarea
                                {...register('target_users')}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    return value.split('\n').filter(Boolean);
                                }}
                            />
                        </FormControl>

                        <FormControl isRequired>
                            <FormLabel>Project Goals (one per line)</FormLabel>
                            <Textarea
                                {...register('goals')}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    return value.split('\n').filter(Boolean);
                                }}
                            />
                        </FormControl>

                        <Button type="submit" colorScheme="blue">
                            Generate Objectives
                        </Button>
                    </VStack>
                </Box>
            ) : (
                <VStack spacing={4}>
                    <Text fontSize="lg" fontWeight="bold">
                        Proposed Objectives
                    </Text>
                    <List spacing={2}>
                        {proposedObjectives.map((objective, index) => (
                            <ListItem key={index}>
                                {objective}
                            </ListItem>
                        ))}
                    </List>
                    <Button onClick={handleObjectiveApproval} colorScheme="green">
                        Approve Objectives
                    </Button>
                </VStack>
            )}
        </Box>
    );
}; 