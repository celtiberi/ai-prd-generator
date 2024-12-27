import React from 'react';
import {
    Box,
    Badge,
    Text,
    VStack,
    HStack,
    List,
    ListItem,
    ListIcon,
    Button,
    useDisclosure,
} from '@chakra-ui/react';
import { MdCheckCircle, MdSettings, MdWarning } from 'react-icons/md';
import { Feature } from '../types';

interface FeatureCardProps {
    feature: Feature;
    onEdit?: (feature: Feature) => void;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({ feature, onEdit }) => {
    const statusColors = {
        draft: 'yellow',
        validated: 'green',
        refined: 'blue'
    };

    const priorityColors = {
        high: 'red',
        medium: 'orange',
        low: 'green'
    };

    return (
        <Box
            borderWidth="1px"
            borderRadius="lg"
            p={4}
            mb={4}
            bg="white"
            shadow="sm"
        >
            <VStack align="stretch" spacing={3}>
                <HStack justify="space-between">
                    <Text fontSize="lg" fontWeight="bold">
                        {feature.name}
                    </Text>
                    <HStack>
                        <Badge colorScheme={statusColors[feature.status]}>
                            {feature.status}
                        </Badge>
                        <Badge colorScheme={priorityColors[feature.priority]}>
                            {feature.priority} priority
                        </Badge>
                    </HStack>
                </HStack>

                <Text color="gray.600">{feature.description}</Text>

                <Box>
                    <Text fontWeight="semibold" mb={2}>Requirements:</Text>
                    <List spacing={2}>
                        {feature.requirements.map((req, index) => (
                            <ListItem key={index}>
                                <ListIcon as={MdCheckCircle} color="green.500" />
                                {req}
                            </ListItem>
                        ))}
                    </List>
                </Box>

                {feature.dependencies.length > 0 && (
                    <Box>
                        <Text fontWeight="semibold" mb={2}>Dependencies:</Text>
                        <List spacing={2}>
                            {feature.dependencies.map((dep, index) => (
                                <ListItem key={index}>
                                    <ListIcon as={MdSettings} color="blue.500" />
                                    {dep}
                                </ListItem>
                            ))}
                        </List>
                    </Box>
                )}

                {feature.feedback && (
                    <Box bg="orange.50" p={3} borderRadius="md">
                        <HStack>
                            <ListIcon as={MdWarning} color="orange.500" />
                            <Text color="orange.800">{feature.feedback}</Text>
                        </HStack>
                    </Box>
                )}

                {onEdit && (
                    <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={() => onEdit(feature)}
                    >
                        Edit Feature
                    </Button>
                )}
            </VStack>
        </Box>
    );
}; 