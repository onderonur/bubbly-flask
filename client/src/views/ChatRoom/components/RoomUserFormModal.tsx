import React, { useMemo, useCallback } from 'react';
import { DialogActions } from '@material-ui/core';
import { SocketUser, ID } from 'types';
import { Formik, FormikConfig } from 'formik';
import * as Yup from 'yup';
import { trimString } from 'utils';
import BaseTextField from 'components/BaseTextField';
import BaseModalForm from 'components/BaseModalForm';
import useSocketIo from 'contexts/SocketIoContext';
import Stack from 'components/Stack';
import BaseColorPicker from 'components/BaseColorPicker';
import BaseDialog from 'components/BaseDialog';
import BaseDialogTitle from 'components/BaseDialog/components/BaseDialogTitle';
import BaseDialogContent from 'components/BaseDialog/components/BaseDialogContent';
import SubmitButton from 'components/SubmitButton';
import BaseButton from 'components/BaseButton';

interface RoomUserFormValues {
  username: string;
  color: string;
}

const validationSchema = Yup.object().shape<RoomUserFormValues>({
  username: Yup.string().label('Username').required().transform(trimString),
  color: Yup.string().label('Color').required(),
});

interface RoomUserFormModalProps {
  roomUser: SocketUser;
  roomId: ID;
  open: boolean;
  onClose: VoidFunction;
}

const RoomUserFormModal = React.memo<RoomUserFormModalProps>(
  function RoomUserFormModal({ roomUser, roomId, open, onClose }) {
    const initialValues = useMemo<RoomUserFormValues>(
      () => ({ username: roomUser.username, color: roomUser.color }),
      [roomUser]
    );

    const io = useSocketIo();

    const handleSubmit = useCallback<
      FormikConfig<RoomUserFormValues>['onSubmit']
    >(
      (values, formikHelpers) => {
        io?.emit('edit user', roomId, values, () => {
          formikHelpers.setSubmitting(false);
          onClose();
        });
      },
      [io, onClose, roomId]
    );

    return (
      <BaseDialog open={open} onClose={onClose} fullWidth responsive>
        <BaseDialogTitle>User Settings</BaseDialogTitle>
        <Formik<RoomUserFormValues>
          initialValues={initialValues}
          validationSchema={validationSchema}
          validateOnMount
          onSubmit={handleSubmit}
        >
          {({ isSubmitting }) => {
            return (
              <BaseModalForm>
                <BaseDialogContent>
                  <Stack flexDirection="column" spacing={2}>
                    <BaseTextField
                      name="username"
                      label="Username"
                      required
                      autoFocus
                      fullWidth
                    />
                    <BaseColorPicker name="color" label="Color" required />
                  </Stack>
                </BaseDialogContent>
                <DialogActions>
                  <BaseButton onClick={onClose}>Cancel</BaseButton>
                  <SubmitButton loading={isSubmitting}>Save</SubmitButton>
                </DialogActions>
              </BaseModalForm>
            );
          }}
        </Formik>
      </BaseDialog>
    );
  }
);

export default RoomUserFormModal;
