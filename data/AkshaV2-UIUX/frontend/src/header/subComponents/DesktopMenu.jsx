import { Button } from "@mui/material";

const DesktopMenu = ({ navigation, onMenuChange }) => {
    return (
        <>
            {navigation.map((page, index) => (
                <Button
                    key={index}
                    onClick={() => onMenuChange(page, index)}
                    sx={{              //if active display white text with blue background else display black text with white background
                        mx: 4,
                        color: page.active ? "white" : "black",
                        display: "block",
                        textTransform: "initial",
                        fontSize: "17px",
                        background: page.active ? "#0A57EB" : "white",
                        "&:hover": {
                            background: page.active ? "#0A57EB" : "white",
                        },
                    }}
                >
                    {page.active === true ? (
                        <img
                            //changes icon image on active change
                            //if active display white icon image(i.e page.iconWhite)  
                            //else display black icon image(i.e page.icon)  
                            src={page.iconWhite}
                            style={{
                                width: page.width,  //dynamic icon based on name and active
                                height: page.height,
                            }}
                            alt="pages icon"
                        />
                    ) : (
                        <img
                            src={page.icon} //dynamic icon based on name and active
                            style={{ 
                                width: page.width,
                                height: page.height,
                            }}
                            alt="pages icon"
                        />
                    )}
                    &nbsp;
                    {page.name}
                </Button>
            ))}
        </>


    );
}

export default DesktopMenu;