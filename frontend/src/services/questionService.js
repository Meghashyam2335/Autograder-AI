const BASE_URL = "http://localhost:5000";

export const getQuestions = async (examId) => {
    const res = await fetch(`${BASE_URL}/get-questions/${examId}`);
    return res.json();
};