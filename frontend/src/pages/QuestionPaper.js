import React, { useEffect, useState } from "react";
import { getQuestions } from "../services/questionService";
import { useParams } from "react-router-dom";

function QuestionPaper() {
    const { examId } = useParams();
    const [questions, setQuestions] = useState({});

    useEffect(() => {
        getQuestions(examId).then(setQuestions);
    }, [examId]);

    return (
        <div>
            <h2>Question Paper</h2>

            {Object.keys(questions).length === 0 ? (
                <p>Loading...</p>
            ) : (
                Object.entries(questions).map(([qid, q]) => (
                    <div key={qid}>
                        <h3>{qid}</h3>
                        <p>{q}</p>
                    </div>
                ))
            )}
        </div>
    );
}

export default QuestionPaper;