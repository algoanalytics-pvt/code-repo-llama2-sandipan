import settings from '../../assets/images/icons/add-new-cam-icon.png';

const Settingss = ({ onSettingsClick }) => {
    return (
        <>

            {window.localStorage.getItem('isLoggedIn') &&
                //show settings if user logins i.e isLoggedIn is true
                <div>
                    {localStorage.getItem('isLoggedIn') === 'true' && (
                        <>
                            <img
                                src={settings}
                                className="mx-2 setting-icon-style"
                                alt="settings"
                                onClick={() => onSettingsClick()}
                            />
                            /
                            {window.location.pathname === "/cameraDirectory" && (
                                //if path='/cameraDirectory'  display blue line below icon
                                <div
                                    className="setting-active-link"
                                ></div>
                            )}
                        </>
                    )}
                </div>
            }
        </>
    );
}

export default Settingss;