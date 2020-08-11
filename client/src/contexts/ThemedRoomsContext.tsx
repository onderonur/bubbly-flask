import React, { useContext } from 'react';
import useSwr from 'swr';
import { Maybe } from 'types';
import { apiUrl } from 'utils';

interface ThemedRoom {
  title: string;
  slug: string;
}

type ThemedRoomsContextValue = Maybe<ThemedRoom[]>;

const ThemedRoomsContext = React.createContext<ThemedRoomsContextValue>(null);

export function useThemedRooms() {
  const value = useContext(ThemedRoomsContext);
  return value;
}

type ThemedRoomsProviderProps = React.PropsWithChildren<{}>;

const fetcher = (url: string) =>
  fetch(`${apiUrl}${url}`).then((response) => response.json());

function ThemedRoomsProvider({ children }: ThemedRoomsProviderProps) {
  const { data } = useSwr<ThemedRoom[]>('/api/rooms/themed', fetcher);

  return (
    <ThemedRoomsContext.Provider value={data}>
      {children}
    </ThemedRoomsContext.Provider>
  );
}

export default ThemedRoomsProvider;
