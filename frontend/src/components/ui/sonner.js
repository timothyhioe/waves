import React from 'react';
import { Toaster as SonnerToaster, toast as sonnerToast } from 'sonner';

export const Toaster = (props) => {
  return <SonnerToaster {...props} />;
};

export const toast = sonnerToast;
