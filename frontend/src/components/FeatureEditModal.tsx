import React from 'react';
import {
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalBody,
    ModalFooter,
    Button,
    FormControl,
    FormLabel,
    Input,
    Textarea,
    Select,
    VStack,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { Feature } from '../types';

interface FeatureEditModalProps {
    feature: Feature;
    isOpen: boolean;
    onClose: () => void;
    onSave: (feature: Feature) => void;
}

export const FeatureEditModal: React.FC<FeatureEditModalProps> = ({
    feature,
    isOpen,
    onClose,
    onSave,
}) => {
    const { register, handleSubmit } = useForm<Feature>({
        defaultValues: feature,
    });

    const onSubmit = (data: Feature) => {
        onSave({ ...data, status: 'refined' });
        onClose();
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
            <ModalOverlay />
            <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
                <ModalHeader>Edit Feature</ModalHeader>
                <ModalBody>
                    <VStack spacing={4}>
                        <FormControl>
                            <FormLabel>Name</FormLabel>
                            <Input {...register('name')} />
                        </FormControl>

                        <FormControl>
                            <FormLabel>Description</FormLabel>
                            <Textarea {...register('description')} />
                        </FormControl>

                        <FormControl>
                            <FormLabel>Requirements (one per line)</FormLabel>
                            <Textarea
                                {...register('requirements')}
                                onChange={(e) => {
                                    const value = e.target.value;
                                    return value.split('\n').filter(Boolean);
                                }}
                                value={feature.requirements.join('\n')}
                            />
                        </FormControl>

                        <FormControl>
                            <FormLabel>Priority</FormLabel>
                            <Select {...register('priority')}>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                            </Select>
                        </FormControl>
                    </VStack>
                </ModalBody>
                <ModalFooter>
                    <Button variant="ghost" mr={3} onClick={onClose}>
                        Cancel
                    </Button>
                    <Button colorScheme="blue" type="submit">
                        Save Changes
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    );
}; 