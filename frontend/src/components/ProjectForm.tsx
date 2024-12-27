import React from 'react';
import { useForm } from 'react-hook-form';
import {
    Box,
    Button,
    FormControl,
    FormLabel,
    Input,
    Textarea,
    VStack,
    useToast,
} from '@chakra-ui/react';
import { projectApi } from '../services/api';
import { useProjectStore } from '../store';
import { Project } from '../types';

export const ProjectForm: React.FC = () => {
    const { register, handleSubmit } = useForm<Project>();
    const setProject = useProjectStore((state) => state.setProject);
    const toast = useToast();

    const onSubmit = async (data: Project) => {
        try {
            const result = await projectApi.initialize(data);
            setProject(data);
            toast({
                title: 'Project initialized',
                status: 'success',
                duration: 3000,
            });
        } catch (error) {
            toast({
                title: 'Error initializing project',
                description: error.message,
                status: 'error',
                duration: 5000,
            });
        }
    };

    return (
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
                    <FormLabel>Objectives (one per line)</FormLabel>
                    <Textarea
                        {...register('objectives')}
                        onChange={(e) => {
                            const value = e.target.value;
                            return value.split('\n').filter(Boolean);
                        }}
                    />
                </FormControl>

                <Button type="submit" colorScheme="blue">
                    Generate PRD
                </Button>
            </VStack>
        </Box>
    );
}; 