const BASE_URL = "http://localhost:5000";

export const uploadQuestionKey = async (data) => {
    const res = await fetch(`${BASE_URL}/upload-key`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    return res.json();
};