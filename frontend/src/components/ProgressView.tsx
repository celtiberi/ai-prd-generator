import React from 'react';
import {
    Box,
    VStack,
    Heading,
    Text,
    Progress,
    Button,
    useToast,
    SimpleGrid,
} from '@chakra-ui/react';
import { useQuery, useMutation } from 'react-query';
import { projectApi } from '../services/api';
import { useProjectStore } from '../store';
import { FeatureCard } from './FeatureCard';
import { Feature } from '../types';

export const ProgressView: React.FC = () => {
    const { project, progress, setProgress, updateFeature } = useProjectStore();
    const toast = useToast();

    // Fetch progress periodically
    const { data, isLoading, error } = useQuery(
        'progress',
        projectApi.getProgress,
        {
            refetchInterval: 5000, // Poll every 5 seconds
            onSuccess: (data) => setProgress(data),
        }
    );

    // Handle feature updates
    const updateMutation = useMutation(
        (feature: Feature) => projectApi.submitFeedback({ features: [feature] }),
        {
            onSuccess: () => {
                toast({
                    title: 'Feedback submitted',
                    status: 'success',
                    duration: 3000,
                });
            },
            onError: (error) => {
                toast({
                    title: 'Error submitting feedback',
                    description: error.message,
                    status: 'error',
                    duration: 5000,
                });
            },
        }
    );

    const handleFeatureEdit = (feature: Feature) => {
        updateFeature(feature);
        updateMutation.mutate(feature);
    };

    const handleDownload = async () => {
        try {
            const prd = await projectApi.downloadPRD();
            // Convert to markdown or desired format
            const blob = new Blob([JSON.stringify(prd, null, 2)], {
                type: 'application/json',
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${project?.title || 'prd'}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            toast({
                title: 'Error downloading PRD',
                description: error.message,
                status: 'error',
                duration: 5000,
            });
        }
    };

    if (isLoading) {
        return (
            <Box p={8}>
                <Progress size="xs" isIndeterminate />
                <Text mt={4}>Loading progress...</Text>
            </Box>
        );
    }

    if (error) {
        return (
            <Box p={8}>
                <Text color="red.500">Error: {error.message}</Text>
            </Box>
        );
    }

    const validatedFeatures = progress?.features.filter(
        (f) => f.status === 'validated'
    );
    const progressPercentage =
        (validatedFeatures?.length || 0) / (progress?.features.length || 1) * 100;

    return (
        <VStack spacing={8} align="stretch">
            <Box>
                <Heading size="lg">{project?.title}</Heading>
                <Text mt={2} color="gray.600">
                    {project?.description}
                </Text>
            </Box>

            <Box>
                <Text mb={2}>Overall Progress</Text>
                <Progress
                    value={progressPercentage}
                    size="lg"
                    colorScheme="blue"
                    hasStripe
                />
            </Box>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                {progress?.features.map((feature) => (
                    <FeatureCard
                        key={feature.name}
                        feature={feature}
                        onEdit={handleFeatureEdit}
                    />
                ))}
            </SimpleGrid>

            <Button
                colorScheme="green"
                size="lg"
                onClick={handleDownload}
                isDisabled={progressPercentage < 100}
            >
                Download PRD
            </Button>
        </VStack>
    );
}; 