import React from 'react';
import Navbar from '@theme-original/Navbar';
import AuthButton from '@site/src/components/Auth/AuthButton';
import type {Props} from '@theme/Navbar';

export default function NavbarWrapper(props: Props): JSX.Element {
  return (
    <>
      <Navbar {...props} />
      <div style={{
        position: 'absolute',
        top: '0',
        right: '180px',
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        zIndex: 100,
      }}>
        <AuthButton />
      </div>
    </>
  );
}
